"""
DS 223 Marketing Analytics - Homework 2: A/B Testing

Student: STUDENT_NAME

Four ad options are compared with two bandit algorithms:
    - Epsilon-Greedy (epsilon = 1/t)
    - Thompson Sampling (Gaussian rewards, known precision)

Run:  python Bandit.py
Files created:
    rewards.csv              {Bandit, Reward, Algorithm}
    learning_epsilon_greedy.png, learning_thompson_sampling.png  (plot1)
    cumulative_comparison.png                           (plot2)
"""
############################### LOGGER
from abc import ABC, abstractmethod
from loguru import logger

import numpy as np
import pandas as pd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

# ---------------- settings ----------------
Bandit_Reward = [1, 2, 3, 4]
NumberOfTrials = 20000
NOISE_PRECISION = 2.0   # known precision of rewards (variance = 0.5)
PRIOR_PRECISION = 0.01  # weak prior for Thompson Sampling
np.random.seed(2026)


class Bandit(ABC):
    ##==== DO NOT REMOVE ANYTHING FROM THIS CLASS ====##

    @abstractmethod
    def __init__(self, p):
        pass

    @abstractmethod
    def __repr__(self):
        pass

    @abstractmethod
    def pull(self):
        pass

    @abstractmethod
    def update(self):
        pass

    @abstractmethod
    def experiment(self):
        pass

    @abstractmethod
    def report(self):
        # store data in csv
        # print average reward (use f strings to make it informative)
        # print average regret (use f strings to make it informative)
        pass

#--------------------------------------#


class Visualization():
    """Plotting helpers for the bandit experiments."""

    def plot1(self, results, title):
        """Plot the learning process of one algorithm: how many times each
        ad was chosen and the running mean reward (linear and log x-axis).

        :param results: trial-level results with columns Bandit, Reward
        :type results: pandas.DataFrame
        :param title: algorithm name used in the title and file name
        :type title: str
        """
        t = np.arange(1, len(results) + 1)
        running_mean = results["Reward"].cumsum() / t

        fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(15, 4))
        for b in Bandit_Reward:
            ax1.plot(t, (results["Bandit"] == b).cumsum(), label=f"Ad {b}")
        ax1.set_title(f"{title}: times each ad was chosen")
        ax1.set_xlabel("Trial")
        ax1.legend()

        ax2.plot(t, running_mean)
        ax2.axhline(max(Bandit_Reward), ls="--", c="red", label="Best possible")
        ax2.set_title(f"{title}: mean reward (linear)")
        ax2.set_xlabel("Trial")
        ax2.legend()

        ax3.plot(t, running_mean)
        ax3.axhline(max(Bandit_Reward), ls="--", c="red", label="Best possible")
        ax3.set_xscale("log")
        ax3.set_title(f"{title}: mean reward (log)")
        ax3.set_xlabel("Trial (log)")
        ax3.legend()

        fig.tight_layout()
        name = f"learning_{title.lower().replace(' ', '_').replace('-', '_')}.png"
        fig.savefig(name)
        plt.close(fig)
        logger.info(f"plot1 saved -> {name}")

    def plot2(self, eg, ts):
        """Compare cumulative rewards and cumulative regrets of
        Epsilon-Greedy and Thompson Sampling.

        :param eg: finished Epsilon-Greedy experiment
        :type eg: EpsilonGreedy
        :param ts: finished Thompson Sampling experiment
        :type ts: ThompsonSampling
        """
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))
        for algo in (eg, ts):
            ax1.plot(np.cumsum(algo.reward_history), label=str(algo.name))
            ax2.plot(np.cumsum(algo.regret_history), label=str(algo.name))
        ax1.set_title("Cumulative reward")
        ax2.set_title("Cumulative regret")
        for ax in (ax1, ax2):
            ax.set_xlabel("Trial")
            ax.legend()
        fig.tight_layout()
        fig.savefig("cumulative_comparison.png")
        plt.close(fig)
        logger.info("plot2 saved -> cumulative_comparison.png")

#--------------------------------------#

class EpsilonGreedy(Bandit):
    """Epsilon-Greedy bandit. At trial t it explores a random ad with
    probability 1/t, otherwise it picks the ad with the highest sample mean.
    """

    def __init__(self, p):
        """
        :param p: true mean reward of every ad
        :type p: list
        """
        self.name = "Epsilon-Greedy"
        self.true_means = np.array(p, dtype=float)
        self.n_ads = len(p)
        self.sample_mean = np.zeros(self.n_ads)
        self.n_pulls = np.zeros(self.n_ads, dtype=int)
        self.t = 0
        self.ad_history, self.reward_history, self.regret_history = [], [], []

    def __repr__(self):
        return (f"{self.name} | trials={self.t} | "
                f"estimated means={np.round(self.sample_mean, 2)}")

    def choose_ad(self):
        """Pick an ad using epsilon = 1/t.

        :return: index of the chosen ad
        :rtype: int
        """
        epsilon = 1 / self.t
        if np.random.rand() < epsilon:
            return np.random.randint(self.n_ads)
        return int(np.argmax(self.sample_mean))

    def pull(self, ad):
        """Show the ad and observe a noisy reward.

        :param ad: index of the ad
        :type ad: int
        :return: reward
        :rtype: float
        """
        return np.random.randn() / np.sqrt(NOISE_PRECISION) + self.true_means[ad]

    def update(self, ad, reward):
        """Update the sample mean of the shown ad.

        :param ad: index of the ad
        :type ad: int
        :param reward: observed reward
        :type reward: float
        """
        self.n_pulls[ad] += 1
        n = self.n_pulls[ad]
        self.sample_mean[ad] = ((n - 1) * self.sample_mean[ad] + reward) / n

    def experiment(self, trials=NumberOfTrials):
        """Run Epsilon-Greedy for the given number of trials.

        :param trials: number of trials
        :type trials: int
        """
        best = self.true_means.max()
        for _ in range(trials):
            self.t += 1
            ad = self.choose_ad()
            r = self.pull(ad)
            self.update(ad, r)
            self.ad_history.append(Bandit_Reward[ad])
            self.reward_history.append(r)
            self.regret_history.append(best - self.true_means[ad])
        logger.debug(self)

    def report(self):
        """Log the summary and return trial-level results.

        :return: DataFrame with columns Bandit, Reward, Algorithm
        :rtype: pandas.DataFrame
        """
        logger.info(f"{self.name} -> cumulative reward = {sum(self.reward_history):,.2f}")
        logger.info(f"{self.name} -> cumulative regret = {sum(self.regret_history):,.2f}")
        logger.info(f"{self.name} -> average reward = {np.mean(self.reward_history):.4f}, "
                    f"average regret = {np.mean(self.regret_history):.4f}")
        logger.info(f"{self.name} -> times each ad was shown = {self.n_pulls.tolist()}")
        return pd.DataFrame({"Bandit": self.ad_history,
                             "Reward": self.reward_history,
                             "Algorithm": self.name})

#--------------------------------------#

class ThompsonSampling(Bandit):
    """Thompson Sampling for Gaussian rewards with known precision.

    Each ad has a Normal prior N(0, 1/PRIOR_PRECISION) on its mean.
    Every reward updates it to a Normal posterior:
        precision_new = precision_old + NOISE_PRECISION
        mean_new = (precision_old * mean_old + NOISE_PRECISION * reward) / precision_new
    """

    def __init__(self, p):
        """
        :param p: true mean reward of every ad
        :type p: list
        """
        self.name = "Thompson Sampling"
        self.true_means = np.array(p, dtype=float)
        self.n_ads = len(p)
        self.post_mean = np.zeros(self.n_ads)
        self.post_precision = np.full(self.n_ads, PRIOR_PRECISION)
        self.n_pulls = np.zeros(self.n_ads, dtype=int)
        self.t = 0
        self.ad_history, self.reward_history, self.regret_history = [], [], []

    def __repr__(self):
        return (f"{self.name} | trials={self.t} | "
                f"posterior means={np.round(self.post_mean, 2)}")

    def choose_ad(self):
        """Sample a mean for every ad from its posterior and pick the largest.

        :return: index of the chosen ad
        :rtype: int
        """
        draws = np.random.randn(self.n_ads) / np.sqrt(self.post_precision) + self.post_mean
        return int(np.argmax(draws))

    def pull(self, ad):
        """Show the ad and observe a noisy reward.

        :param ad: index of the ad
        :type ad: int
        :return: reward
        :rtype: float
        """
        return np.random.randn() / np.sqrt(NOISE_PRECISION) + self.true_means[ad]

    def update(self, ad, reward):
        """Bayesian update of the shown ad's posterior.

        :param ad: index of the ad
        :type ad: int
        :param reward: observed reward
        :type reward: float
        """
        self.n_pulls[ad] += 1
        old_prec = self.post_precision[ad]
        new_prec = old_prec + NOISE_PRECISION
        self.post_mean[ad] = (old_prec * self.post_mean[ad] + NOISE_PRECISION * reward) / new_prec
        self.post_precision[ad] = new_prec

    def experiment(self, trials=NumberOfTrials):
        """Run Thompson Sampling for the given number of trials.

        :param trials: number of trials
        :type trials: int
        """
        best = self.true_means.max()
        for _ in range(trials):
            self.t += 1
            ad = self.choose_ad()
            r = self.pull(ad)
            self.update(ad, r)
            self.ad_history.append(Bandit_Reward[ad])
            self.reward_history.append(r)
            self.regret_history.append(best - self.true_means[ad])
        logger.debug(self)

    def report(self):
        """Log the summary and return trial-level results.

        :return: DataFrame with columns Bandit, Reward, Algorithm
        :rtype: pandas.DataFrame
        """
        logger.info(f"{self.name} -> cumulative reward = {sum(self.reward_history):,.2f}")
        logger.info(f"{self.name} -> cumulative regret = {sum(self.regret_history):,.2f}")
        logger.info(f"{self.name} -> average reward = {np.mean(self.reward_history):.4f}, "
                    f"average regret = {np.mean(self.regret_history):.4f}")
        logger.info(f"{self.name} -> times each ad was shown = {self.n_pulls.tolist()}")
        return pd.DataFrame({"Bandit": self.ad_history,
                             "Reward": self.reward_history,
                             "Algorithm": self.name})




def comparison():
    """Run both algorithms, save results to CSV, draw the plots and
    log a short comparison.
    """
    eg = EpsilonGreedy(Bandit_Reward)
    ts = ThompsonSampling(Bandit_Reward)

    logger.info(f"Starting experiment: {NumberOfTrials} trials, ads = {Bandit_Reward}")
    eg.experiment()
    ts.experiment()

    results = pd.concat([eg.report(), ts.report()], ignore_index=True)
    results.to_csv("rewards.csv", index=False)
    logger.info(f"rewards.csv saved ({len(results)} rows)")

    viz = Visualization()
    viz.plot1(results[results["Algorithm"] == eg.name].reset_index(drop=True), eg.name)
    viz.plot1(results[results["Algorithm"] == ts.name].reset_index(drop=True), ts.name)
    viz.plot2(eg, ts)

    diff = sum(eg.regret_history) - sum(ts.regret_history)
    if diff > 0:
        logger.success(f"Thompson Sampling had {diff:,.0f} less regret than Epsilon-Greedy")
    else:
        logger.success(f"Epsilon-Greedy had {-diff:,.0f} less regret than Thompson Sampling")


if __name__=='__main__':

    comparison()
