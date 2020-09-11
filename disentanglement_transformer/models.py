from torch.utils.tensorboard import SummaryWriter
import torch
from tqdm import tqdm

from disentanglement_transformer.h_params import *
from components.bayesnets import BayesNet
from components.criteria import Supervision


# ==================================================== SSPOSTAG MODEL CLASS ============================================

class DisentanglementTransformerVAE(nn.Module, metaclass=abc.ABCMeta):
    def __init__(self, vocab_index, tag_index, h_params, autoload=True, wvs=None):
        super(DisentanglementTransformerVAE, self).__init__()

        self.h_params = h_params
        self.word_embeddings = nn.Embedding(h_params.vocab_size, h_params.embedding_dim)
        nn.init.uniform_(self.word_embeddings.weight, -1., 1.)
        if wvs is not None:
            self.word_embeddings.weight.data.copy_(wvs)
            #self.word_embeddings.weight.requires_grad = False

        # Getting vertices
        vertices, _, self.generated_v = h_params.graph_generator(h_params, self.word_embeddings)

        # Instanciating inference and generation networks
        self.infer_bn = BayesNet(vertices['infer'])
        self.infer_last_states = None
        self.infer_last_states_test = None
        self.gen_bn = BayesNet(vertices['gen'])
        self.gen_last_states = None
        self.gen_last_states_test = None

        # Setting up categorical variable indexes
        self.index = {self.generated_v: vocab_index}

        # The losses
        self.losses = [loss(self, w) for loss, w in zip(h_params.losses, h_params.loss_params)]
        self.iw = any([isinstance(loss, IWLBo) for loss in self.losses])
        if self.iw:
            assert any([lv.iw for lv in self.infer_bn.variables]), "When using IWLBo, at least a variable in the " \
                                                                   "inference graph must be importance weighted."

        # The Optimizer
        self.optimizer = h_params.optimizer(self.parameters(), **h_params.optimizer_kwargs)

        # Getting the Summary writer
        self.writer = SummaryWriter(h_params.viz_path)
        self.step = 0

        # Loading previous checkpoint if auto_load is set to True
        if autoload:
            self.load()

    def opt_step(self, samples):
        if (self.step % self.h_params.grad_accumulation_steps) == 0:
            # Reinitializing gradients if accumulation is over
            self.optimizer.zero_grad()
        #                          ----------- Unsupervised Forward/Backward ----------------
        # Forward pass
        infer_inputs = {'x': samples['x'],  'x_prev': samples['x_prev']}
        if self.iw:  # and (self.step >= self.h_params.anneal_kl[0]):
            self.infer_last_states = self.infer_bn(infer_inputs, n_iw=self.h_params.training_iw_samples,
                                                   prev_states=self.infer_last_states, complete=True)
        else:
            self.infer_last_states = self.infer_bn(infer_inputs, prev_states=self.infer_last_states, complete=True)
        gen_inputs = {**{k.name: v for k, v in self.infer_bn.variables_hat.items()},
                      **{'x': samples['x'], 'x_prev': samples['x_prev']}}
        if self.iw:
            gen_inputs = self._harmonize_input_shapes(gen_inputs, self.h_params.training_iw_samples)
        if self.step < self.h_params.anneal_kl[0]:
            self.gen_last_states = self.gen_bn(gen_inputs, target=self.generated_v,
                                               prev_states=self.gen_last_states)
        else:
            self.gen_last_states = self.gen_bn(gen_inputs, prev_states=self.gen_last_states)

        # Loss computation and backward pass
        losses_uns = [loss.get_loss() * loss.w for loss in self.losses if not isinstance(loss, Supervision)]
        sum(losses_uns).backward()
        if not self.h_params.contiguous_lm:
            self.infer_last_states, self.gen_last_states = None, None

        if (self.step % self.h_params.grad_accumulation_steps) == (self.h_params.grad_accumulation_steps-1):
            # Applying gradients and gradient clipping if accumulation is over
            torch.nn.utils.clip_grad_norm_(self.parameters(), self.h_params.grad_clip)
            self.optimizer.step()
        self.step += 1

        self._dump_train_viz()
        total_loss = sum(losses_uns)

        return total_loss

    def forward(self, samples, eval=False, prev_states=None, force_iw=None):
        # Just propagating values through the bayesian networks to get summaries
        if prev_states:
            infer_prev, gen_prev = prev_states
        else:
            infer_prev, gen_prev = None, None

        #                          ----------- Unsupervised Forward/Backward ----------------
        # Forward pass
        infer_inputs = {'x': samples['x'],  'x_prev': samples['x_prev']}

        infer_prev = self.infer_bn(infer_inputs, n_iw=self.h_params.testing_iw_samples, eval=eval,
                                   prev_states=infer_prev, force_iw=force_iw, complete=True)
        gen_inputs = {**{k.name: v for k, v in self.infer_bn.variables_hat.items()},
                      **{'x': samples['x'], 'x_prev': samples['x_prev']}}
        if self.iw or force_iw:
            gen_inputs = self._harmonize_input_shapes(gen_inputs, self.h_params.testing_iw_samples)
        if self.step < self.h_params.anneal_kl[0]:
            gen_prev = self.gen_bn(gen_inputs, target=self.generated_v, eval=eval, prev_states=gen_prev,
                                   complete=True)
        else:
            gen_prev = self.gen_bn(gen_inputs, eval=eval, prev_states=gen_prev, complete=True)

        # Loss computation and backward pass
        [loss.get_loss() * loss.w for loss in self.losses if not isinstance(loss, Supervision)]

        if self.h_params.contiguous_lm:
            return infer_prev, gen_prev
        else:
            return None, None

    def _dump_train_viz(self):
        # Dumping gradient norm
        if (self.step % self.h_params.grad_accumulation_steps) == (self.h_params.grad_accumulation_steps - 1):
            z_gen = [var for var in self.gen_bn.variables if var.name == 'z1'][0]
            for module, name in zip([self, self.infer_bn, self.gen_bn,
                                     self.gen_bn.approximator[z_gen] if z_gen in self.gen_bn.approximator else None],
                                    ['overall', 'inference', 'generation', 'prior']):
                if module is None: continue
                grad_norm = 0
                for p in module.parameters():
                    if p.grad is not None:
                        param_norm = p.grad.data.norm(2)
                        grad_norm += param_norm.item() ** 2
                grad_norm = grad_norm ** (1. / 2)
                self.writer.add_scalar('train' + '/' + '_'.join([name, 'grad_norm']), grad_norm, self.step)

        # Getting the interesting metrics: this model's loss and some other stuff that would be useful for diagnosis
        for loss in self.losses:
            for name, metric in loss.metrics().items():
                self.writer.add_scalar('train' + name, metric, self.step)

    def dump_test_viz(self, complete=False):
        if complete:
            print('Performing complete test')
        # Getting the interesting metrics: this model's loss and some other stuff that would be useful for diagnosis
        for loss in self.losses:
            for name, metric in loss.metrics().items():
                self.writer.add_scalar('test' + name, metric, self.step)

        summary_dumpers = {'scalar': self.writer.add_scalar, 'text': self.writer.add_text,
                           'image': self.writer.add_image}

        # We limit the generation of these samples to the less frequent "complete" test visualisations because their
        # computational cost may be high, and because the make the log file a lot larger.
        if complete and any([isinstance(loss, ELBo) for loss in self.losses]):
            for summary_type, summary_name, summary_data in self.data_specific_metrics():
                summary_dumpers[summary_type]('test'+summary_name, summary_data, self.step)

    def data_specific_metrics(self):
        # this is supposed to output a list of (summary type, summary name, summary data) triplets
        with torch.no_grad():
            summary_triplets = [
                ('text', '/ground_truth', self.decode_to_text(self.gen_bn.variables_star[self.generated_v])),
                ('text', '/reconstructions', self.decode_to_text(self.generated_v.post_params['logits'])),
            ]

            n_samples = sum(self.h_params.n_latents)
            repeats = 2
            go_symbol = torch.ones([n_samples*repeats + 2 + (2 if 'zlstm' in self.gen_bn.name_to_v else 0)]).long() * \
                        self.index[self.generated_v].stoi['<go>']
            go_symbol = go_symbol.to(self.h_params.device).unsqueeze(-1)
            x_prev = go_symbol
            temp = 1.0
            only_z_sampling = True
            gen_len = self.h_params.max_len * (3 if self.h_params.contiguous_lm else 1)
            z_gen = self.gen_bn.name_to_v['z1']
            # When z_gen is independent from X_prev (sequence level z)
            if z_gen not in self.gen_bn.parent:
                if not (type(self.h_params.n_latents) == int and self.h_params.n_latents == 1):
                    orig_z_sample_1 = z_gen.prior_sample((1,))[0]
                    orig_z_sample_2 = z_gen.prior_sample((1,))[0]
                    z_sample_1 = orig_z_sample_1.repeat(n_samples+1+(1 if 'zlstm' in self.gen_bn.name_to_v else 0), 1)
                    z_sample_2 = orig_z_sample_2.repeat(n_samples+1+(1 if 'zlstm' in self.gen_bn.name_to_v else 0), 1)
                    for i in range(1, self.h_params.n_latents[0]+1):
                        start, end = int((i-1) * self.h_params.z_size / max(self.h_params.n_latents)), \
                                     int(i * self.h_params.z_size / max(self.h_params.n_latents))
                        z_sample_1[i, ..., start:end] = orig_z_sample_2[0, ..., start:end]
                        z_sample_2[i, ..., start:end] = orig_z_sample_1[0, ..., start:end]
                    z_sample = [z_sample_1, z_sample_2]
                    z_sample = torch.cat(z_sample)
                    z_input = {'z1': z_sample.unsqueeze(1)}
                    # Structured Z case
                    z1, z2 = self.gen_bn.name_to_v['z2'], self.gen_bn.name_to_v['z3']
                    self.gen_bn({'z1': orig_z_sample_1.unsqueeze(1),
                                 'x_prev':torch.zeros((1, 1, self.generated_v.size)).to(self.h_params.device)})
                    orig_z1_sample_1, orig_z2_sample_1 = z1.post_samples.squeeze(1), z2.post_samples.squeeze(1)
                    orig_z1_params_1, orig_z2_params_1 = z1.post_params, z2.post_params
                    z1_sample_1 = orig_z1_sample_1.repeat(n_samples+1+(1 if 'zlstm' in self.gen_bn.name_to_v else 0), 1)
                    z2_sample_1 = orig_z2_sample_1.repeat(n_samples+1+(1 if 'zlstm' in self.gen_bn.name_to_v else 0), 1)
                    self.gen_bn({'z1': orig_z_sample_1.unsqueeze(1),
                                 'x_prev':torch.zeros((1, 1, self.generated_v.size)).to(self.h_params.device)})
                    orig_z1_sample_2, orig_z2_sample_2 = z1.post_samples.squeeze(1), z2.post_samples.squeeze(1)
                    orig_z1_params_2, orig_z2_params_2 = z1.post_params, z2.post_params
                    z1_sample_2 = orig_z1_sample_2.repeat(n_samples+1+(1 if 'zlstm' in self.gen_bn.name_to_v else 0), 1)
                    z2_sample_2 = orig_z2_sample_2.repeat(n_samples+1+(1 if 'zlstm' in self.gen_bn.name_to_v else 0), 1)
                    z1_offset = self.h_params.n_latents[0]
                    for i in range(1, self.h_params.n_latents[1]+1):
                        start, end = int((i-1) * self.h_params.z_size / max(self.h_params.n_latents)), \
                                     int(i * self.h_params.z_size / max(self.h_params.n_latents))
                        z1_sample_1[z1_offset+i, ..., start:end] = orig_z1_sample_2[0, ..., start:end]
                        z1_sample_2[z1_offset+i, ..., start:end] = orig_z1_sample_1[0, ..., start:end]
                    z2_offset = self.h_params.n_latents[0] + self.h_params.n_latents[1]
                    for i in range(1, self.h_params.n_latents[2]+1):
                        start, end = int((i-1) * self.h_params.z_size / max(self.h_params.n_latents)), \
                                     int(i * self.h_params.z_size / max(self.h_params.n_latents))
                        z2_sample_1[z2_offset+i, ..., start:end] = orig_z2_sample_2[0, ..., start:end]
                        z2_sample_2[z2_offset+i, ..., start:end] = orig_z2_sample_1[0, ..., start:end]
                    z1_sample = [z1_sample_1, z1_sample_2]
                    z2_sample = [z2_sample_1, z2_sample_2]
                    z1_sample = torch.cat(z1_sample)
                    z2_sample = torch.cat(z2_sample)
                    z_input['z2'] = z1_sample.unsqueeze(1)
                    z_input['z3'] = z2_sample.unsqueeze(1)


                else:
                    z_sample = z_gen.prior_sample((n_samples, ))[0]
                    z_input = {'z1': z_sample.unsqueeze(1)}
            else:
                z_input = {}
            if ('zlstm' in self.gen_bn.name_to_v) and (self.gen_bn.name_to_v['zlstm'] not in self.gen_bn.parent):
                # case where zlstm is independant of z
                # Special case where generation is not autoregressive
                zlstm = self.gen_bn.name_to_v['zlstm']
                zlstm_sample1 = zlstm.prior_sample((1,))[0]
                zlstm_sample2 = zlstm.prior_sample((1,))[0]
                zlstm_sample = torch.cat([zlstm_sample1.repeat(n_samples+1, 1), zlstm_sample2,
                                          zlstm_sample2.repeat(n_samples+1, 1), zlstm_sample1], 0)
                self.gen_bn({'z1': z_sample.unsqueeze(1).expand(z_sample.shape[0], gen_len, z_sample.shape[1]),
                             'zlstm': zlstm_sample.unsqueeze(1).expand(z_sample.shape[0], gen_len, z_sample.shape[1])})
                samples_i = self.generated_v.post_params['logits']
                x_prev = torch.argmax(samples_i, dim=-1)

            else:
                # Normal Autoregressive generation
                for i in range(gen_len):
                    self.gen_bn({'x_prev': x_prev, **{k: v.expand(v.shape[0], i+1, v.shape[-1])
                                                      for k, v in z_input.items()}})
                    if only_z_sampling:
                        samples_i = self.generated_v.post_params['logits']
                    else:
                        samples_i = self.generated_v.posterior(logits=self.generated_v.post_params['logits'],
                                                               temperature=temp).rsample()
                    x_prev = torch.cat([x_prev, torch.argmax(samples_i,     dim=-1)[..., -1].unsqueeze(-1)],
                                       dim=-1)

            summary_triplets.append(
                ('text', '/prior_sample', self.decode_to_text(x_prev, gen=True)))

        return summary_triplets

    def decode_to_text(self, x_hat_params, gen=False):
        # It is assumed that this function is used at test time for display purposes
        # Getting the argmax from the one hot if it's not done
        while x_hat_params.shape[-1] == self.h_params.vocab_size and x_hat_params.ndim > 3:
            x_hat_params = x_hat_params.mean(0)
        while x_hat_params.ndim > 2 and x_hat_params.shape[-1] != self.h_params.vocab_size:
            x_hat_params = x_hat_params[0]
        if x_hat_params.shape[-1] == self.h_params.vocab_size:
            x_hat_params = torch.argmax(x_hat_params, dim=-1)
        assert x_hat_params.ndim == 2, "Mis-shaped generated sequence: {}".format(x_hat_params.shape)
        if not gen:
            text = ' |||| '.join([' '.join([self.index[self.generated_v].itos[w]
                                            for w in sen])#.split('<eos>')[0]
                                  for sen in x_hat_params]).replace('<pad>', '_').replace('_unk', '<?>').replace('<eos>', '\n')
        else:
            samples = [' '.join([self.index[self.generated_v].itos[w]
                                 for w in sen]).split('<eos>')[0].replace('<go>', '').replace('</go>', '')
                       for sen in x_hat_params]
            first_sample, second_sample = samples[:int(len(samples)/2)], samples[int(len(samples) / 2):]
            samples = ['**First Sample**\n'] + \
                      [(str(i) if sample == first_sample[0] else '**'+str(i)+'**') + ': ' +
                       sample for i, sample in enumerate(first_sample)] + \
                      ['**Second Sample**\n'] + \
                      [(str(i) if sample == second_sample[0] else '**'+str(i)+'**') + ': ' +
                       sample for i, sample in enumerate(second_sample)]
            text = ' |||| '.join(samples).replace('<pad>', '_').replace('_unk', '<?>')

        return text

    def get_perplexity(self, iterator):
        with torch.no_grad():
            neg_log_perplexity_lb = 0
            total_samples = 0
            infer_prev, gen_prev = None, None
            force_iw = ['z3' if 'z3' in self.infer_bn.name_to_v else 'z1']
            iwlbo = IWLBo(self, 1)
            for i, batch in enumerate(tqdm(iterator, desc="Getting Model Perplexity")):
                if batch.text.shape[1] < 2: continue
                infer_prev, gen_prev = self({'x': batch.text[..., 1:],
                                             'x_prev': batch.text[..., :-1]}, prev_states=(infer_prev, gen_prev),
                                            force_iw=force_iw,
                                            )
                if not self.h_params.contiguous_lm:
                    infer_prev, gen_prev = None, None
                elbo = - iwlbo.get_loss(actual=True)
                total_samples_i = torch.sum(batch.text != self.h_params.vocab_ignore_index)
                neg_log_perplexity_lb += elbo * total_samples_i

                total_samples += total_samples_i

            neg_log_perplexity_lb /= total_samples
            perplexity_ub = torch.exp(- neg_log_perplexity_lb)

            self.writer.add_scalar('test/PerplexityUB', perplexity_ub, self.step)
            return perplexity_ub

    def save(self):
        root = ''
        for subfolder in self.h_params.save_path.split(os.sep)[:-1]:
            root = os.path.join(root, subfolder)
            if not os.path.exists(root):
                os.mkdir(root)
        torch.save({'model_checkpoint': self.state_dict(), 'step': self.step}, self.h_params.save_path)
        print("Model {} saved !".format(self.h_params.test_name))

    def load(self):
        if os.path.exists(self.h_params.save_path):
            checkpoint = torch.load(self.h_params.save_path)
            model_checkpoint, self.step = checkpoint['model_checkpoint'], checkpoint['step']
            self.load_state_dict(model_checkpoint)
            print("Loaded model at step", self.step)
        else:
            print("Save file doesn't exist, the model will be trained from scratch.")

    def reduce_lr(self, factor):
        for param_group in self.optimizer.param_groups:
            param_group['lr'] /= factor

    def _harmonize_input_shapes(self, gen_inputs, n_iw):
        # This function repeats inputs to the generation network so that they all have the same shape
        max_n_dims = max([val.ndim for val in gen_inputs.values()])
        for k, v in gen_inputs.items():
            actual_v_ndim = v.ndim + (1 if v.dtype == torch.long else 0)
            for _ in range(max_n_dims-actual_v_ndim):
                expand_arg = [n_iw]+list(gen_inputs[k].shape)
                gen_inputs[k] = gen_inputs[k].unsqueeze(0).expand(expand_arg)
        return gen_inputs

# ======================================================================================================================

