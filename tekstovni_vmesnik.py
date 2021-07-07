from errors import AlreadyShot, OutOfRange
import battlefield

def TwoPlayer():
	P = [None, None]
	P[0] = battlefield.Battlefield()
	P[1] = battlefield.Battlefield()
	P[0].RandomSetup()
	P[1].RandomSetup()
	player = 0
	while all(P[x].Poteka() for x in [0, 1]):
		print(f"Na potezi je igralec {player + 1}.")
		try:
			if player:
				P[1].RandomAI()
			else:
				x = int(input("> Vnesite prvo koordinato: "))
				y = int(input("> Vnesite drugo koordinato: "))
				P[player].Shoot(x,y)
			print(P[player])
			player = 1 - player
		except AlreadyShot:
			print("Na to polje ste že streljali. Poskusite ponovno!")
		except OutOfRange:
			print("Izbrano polje ni veljavno. Poskusite ponovno!")

TwoPlayer()