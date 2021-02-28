import gym 
from stable_baselines import PPO2
from stable_baselines.common.policies import MlpPolicy
from stable_baselines.common.evaluation import evaluate_policy
env = gym.make('MountainCar-v0')
#env.render()
agent = PPO2(MlpPolicy, env, verbose=1)

print("Agent created")

agent.learn(total_timesteps = 1000)

eval_env = gym.make('MountainCar-v0')
mean_reward, stddev_reward = evaluate_policy(agent, eval_env, n_eval_episodes = 100)

print("Mean reward:", mean_reward)
print("Std reward:",stddev_reward)


