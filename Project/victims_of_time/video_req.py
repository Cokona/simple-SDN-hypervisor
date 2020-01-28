import vlc
import pafy
import urllib.request

url = "https://www.youtube.com/watch?v=9W3A34TTxFU&list=RD9W3A34TTxFU&start_radio=1"
video = pafy.new(url)
best = video.getbest()
playurl = best.url
ins = vlc.Instance()
player = ins.media_player_new()

code = urllib.request.urlopen(url).getcode()
if str(code).startswith('2') or str(code).startswith('3'):
    print('Stream is working')
else:
    print('Stream is dead')

Media = ins.media_new(playurl)
Media.get_mrl()
player.set_media(Media)
player.play()

good_states = ["State.Playing", "State.NothingSpecial", "State.Opening"]
while str(player.get_state()) in good_states:
    print('Stream is working. Current state = {}'.format(player.get_state()))

print('Stream is not working. Current state = {}'.format(player.get_state()))
player.stop()