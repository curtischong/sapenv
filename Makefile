train:
	python main.py
train-local:
	python main.py --batch_size=4
finetune:
	python main.py --finetune ./models/rl_model_2048_steps.zip
eval:
	python main.py --task=eval --nb_games=1