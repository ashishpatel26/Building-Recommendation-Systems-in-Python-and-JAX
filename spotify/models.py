# Copyright 2023 Hector Yee, Bryan Bischoff
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Models for the spotify million playlist."""

from functools import partial
from typing import Any, Callable, Sequence, Tuple

from flax import linen as nn
import jax.numpy as jnp

class SpotifyModel(nn.Module):
    """Spotify model that takes a context and predicts the next tracks."""
    feature_size : int

    def setup(self):
        self.track_embed = nn.Embed(2262292, self.feature_size)
        self.album_embed = nn.Embed(734684, self.feature_size)
        self.artist_embed = nn.Embed(295860, self.feature_size)

    def get_embeddings(self, track, album, artist):
        """
        Given track, album, artist indices return the embeddings.
        Args:
            track: ints of shape nx1
            album: ints of shape nx1
            artist: ints of shape nx1
        Returns:
            Embeddings representing the track.
        """

        track_embed = self.track_embed(track)
        album_embed = self.album_embed(album)
        artist_embed = self.artist_embed(artist)
        result = jnp.concatenate([track_embed, album_embed, artist_embed], axis=-1)
        return result

    def __call__(self,
                 track_context, album_context, artist_context,
                 next_track, next_album, next_artist):
        """Returns the affinity score to the context.
        Args:
            track_context: ints of shape nx1
            album_context: ints of shape nx1
            artist_context: ints of shape nx1
            next_track: int of shape k
            next_album: int of shape k
            next_artist: int of shape k
        Returns:
            affinity: the affinity of the context to the next track of shape k.
        """
        context_embed = self.get_embeddings(track_context, album_context, artist_context)
        next_embed = self.get_embeddings(next_track, next_album, next_artist)

        # The affinity of the context to the next track is simply the dot product of
        # each context embedding with the next track's embedding.
        affinity = jnp.dot(next_embed, context_embed.T)

        # We then return the max affinity of the context to the next track.
        affinity = jnp.max(affinity, axis = -1)
        return affinity