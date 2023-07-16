.PHONY: image push run

image:
	make -C build image

push:
	make -C build push
	
run:
	kopf run main.py --verbose
