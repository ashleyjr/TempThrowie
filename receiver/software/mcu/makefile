all:
	sdcc  -c ../../../modelling/receiver_pll/receiver_pll.c 	
	sdcc  src/main.c receiver_pll.rel -I inc/ -I ../../../modelling/receiver_pll.c --iram-size 256 --xram-size 256 	

clean:
	rm -f *.o
	rm -f *.asm
	rm -f *.ihx
	rm -f *.lk
	rm -f *.lst
	rm -f *.map
	rm -f *.mem
	rm -f *.rel
	rm -f *.rst
	rm -f *.sym
