import uuid
import time
import secrets
import warnings

from typing import Final, Callable

__all__ = ["UUIDv7Generator", "uuid7"]

NS_IN_MS: Final = 10**6

V7_VER: Final = 0b0111
V7_VAR: Final = 0b10

V7_RAND_A_NUM_BITS: Final = 12

SLEEP_TIME: Final = NS_IN_MS / 2**V7_RAND_A_NUM_BITS / 10**9

# rand_b is 62 bits long total, if we only fill 61 bits with random data then
# we're very unlikely to overflow it even if we have a large random number that
# we use for the increment.
V7_RAND_B_NUM_BITS: Final = 62
V7_RAND_B_RND_BITS: Final = 62

# This is really the only "arbitrary" constant that could be tuneable.
# Determines the size of the random number to increment rand_b by when
# there's a timestamp collision.
V7_RAND_B_INC_BITS: Final = 31


class UUIDv7Generator:
    prev_rand_a = -1
    prev_rand_b = -1
    prev_uuid_int = -1
    prev_unix_time_ms = -1

    unix_time_ns_func: Callable[..., int] = time.time_ns
    randbits_func: Callable[[int], int] = secrets.randbits

    def __call__(self):
        unix_time_ns = self.unix_time_ns_func()

        unix_time_ms, remainder_ns = divmod(unix_time_ns, NS_IN_MS)

        # rand_a is used to provide further clock precision as
        # precribed in the section 'Replace Left-Most Random Bits with Increased
        # Clock Precision (Method 3)' of the RFC:
        # https://www.ietf.org/archive/id/draft-ietf-uuidrev-rfc4122bis-05.html#section-6.2-5.6.1
        rand_a = int((remainder_ns / NS_IN_MS) * (2**V7_RAND_A_NUM_BITS))

        if (unix_time_ms, rand_a) > (self.prev_unix_time_ms, self.prev_rand_a):
            # The normal case: the time data is new so we generate new random
            # data for rand_b
            rand_b = self.randbits_func(V7_RAND_B_RND_BITS)
        else:
            # If the clock has gone backwards, or (vanishingly unlikely) the
            # code has gone fast enough that the time hasn't ticked forward,
            # we increment rand_b by a random amount. Details in the section
            # Monotonic Random (Method 2) in the rfc:
            #
            # https://www.ietf.org/archive/id/draft-ietf-uuidrev-rfc4122bis-05.html#section-6.2-5.4.1

            # use the prior timestamp
            unix_time_ms = self.prev_unix_time_ms
            rand_a = self.prev_rand_a

            # use the prior rand_b but increment it by a random amount.
            increment = self.randbits_func(V7_RAND_B_INC_BITS) + 1
            rand_b = self.prev_rand_b + increment

            if rand_b >= (1 << (V7_RAND_B_NUM_BITS + 1)) - 1:
                # On the average case, we'd have had to increment rand_b over
                # a billion times (i.e. generate a billion UUIDs without the
                # clock stepping forward) for this to happen. If it *does*
                # happen, the RFC suggests in 'Counter Rollover Handling'
                # that the generator should freeze.

                # This call only tries to sleep for 500ns, but in practice the
                # call to sleep() seems to take over 3000ns so the clock REALLY
                # should have ticked by then!
                warnings.warn(
                    "The uuid7 generation counter has overflowed. This shouldn't "
                    "be possible unless the system clock is misbahaving/going backward."
                )
                time.sleep(SLEEP_TIME)
                return self()
        uuid_int = (
            (unix_time_ms << 80)
            | (V7_VER << 76)
            | (rand_a << 64)
            | (V7_VAR << 62)
            | (rand_b)
        )

        assert self.prev_uuid_int < uuid_int, (
            "Generated a UUID that was not greater than the previous:\n"
            f"{uuid.UUID(int=self.prev_uuid_int)}\n{uuid.UUID(int=uuid_int)}"
        )
        self.prev_uuid_int = uuid_int
        self.prev_unix_time_ms = unix_time_ms
        self.prev_rand_a = rand_a
        self.prev_rand_b = rand_b

        return uuid.UUID(int=uuid_int)


uuid7 = UUIDv7Generator()


def get_uuid7():
    return uuid7()
