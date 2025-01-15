from django.db import models
from django.contrib.auth.models import User

class Lists(models.Model):
  title = models.CharField(max_length=255)
  image = models.ImageField(default='default.jpg', upload_to='list_images')
  description = models.TextField(default=None, blank=True)
  dateCreated = models.DateField()
  createdBy = models.CharField(max_length=255)
  allowVotes = models.BooleanField(default=False)
  allowAdds = models.BooleanField(default=False)
  listsongs = models.ManyToManyField('Songs', through='ListSong')


  def __str__(self):
      return f"{self.title} - {self.createdBy}"

  class Meta:
      verbose_name_plural = "Lists"

class Songs(models.Model):
    
    song_title = models.CharField(max_length=500)
    song_artist = models.CharField(max_length=500)
    votes = models.IntegerField(default=0)
    songlists = models.ManyToManyField('Lists', through='ListSong')
    
    def __str__(self):
      return f"{self.song_title} - {self.song_artist}"

    class Meta:
      verbose_name_plural = "Songs"
    
    

class ListSong(models.Model):
    list = models.ForeignKey(Lists, on_delete=models.RESTRICT)
    song = models.ForeignKey(Songs, on_delete=models.RESTRICT)
    

    class Meta:
      verbose_name_plural = "ListSong"


class Vote(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    list = models.ForeignKey(Lists, on_delete=models.CASCADE)
    song = models.ForeignKey(Songs, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} voted for {self.song.id}"