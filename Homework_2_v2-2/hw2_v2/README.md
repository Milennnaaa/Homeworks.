# Homework 2 – A/B Testing (DS 223)

**Student:** STUDENT_NAME

## Task
We have 4 ads with mean rewards `[1, 2, 3, 4]` and run 20,000 trials to find the best ad using:
- **Epsilon-Greedy** with `epsilon = 1/t`
- **Thompson Sampling** with known precision (noise precision = 2, prior N(0, 1/0.01))

## Run
```bash
pip install -r requirements.txt
python Bandit.py
```

## Output files
- `rewards.csv` – every trial with columns `Bandit, Reward, Algorithm`
- `learning_epsilon_greedy.png`, `learning_thompson_sampling.png` – learning process of each algorithm (how often each ad was picked + mean reward on linear and log scale)
- `cumulative_comparison.png` – cumulative reward and cumulative regret of both algorithms

Cumulative reward and regret are printed in the terminal with loguru.

## Results (seed 2026)
| | Cumulative reward | Cumulative regret | Times best ad shown |
|---|---|---|---|
| Epsilon-Greedy | 80,058.81 | 15 | 19,992 |
| Thompson Sampling | 80,097.64 | 22 | 19,984 |

Both algorithms found ad 4 very fast. In this run Epsilon-Greedy has a bit less regret, but this is luck. It found ad 4 early, and with `1/t` it almost stops exploring after that. With another seed it can get stuck on ad 3 for thousands of trials. Thompson Sampling is more stable because it explores based on how unsure it is about each ad.

## Bonus – how to make it better
- **Run many times, not once.** Repeat the experiment with ~100 seeds and compare average regret. One run can be misleading, like here.
- **Fix the epsilon schedule.** `1/t` is too fast. Show every ad a few times first, or use something like `epsilon = 5/t` capped at 1.
- **Add UCB1** as a third method. It has no random exploration and usually has low regret.
- **Don't assume the noise.** In real ad data the variance is unknown, so Thompson Sampling with a Normal-Gamma prior is more realistic.
- **Use real ad metrics.** Real ads have click / no click outcomes, so a Bernoulli bandit with a Beta prior fits better.
- **Less repeated code.** `pull`, `experiment` and `report` are the same in both classes and could live in one shared parent class.
