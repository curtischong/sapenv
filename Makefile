train:
	python main.py
finetune:
	python main.py --finetune ./models/rl_model.zip
eval:
	python main.py --task=eval --nb_games=1