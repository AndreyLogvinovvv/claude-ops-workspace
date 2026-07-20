"""Find all prime numbers up to N using the Sieve of Eratosthenes."""
import sys


def primes_up_to(n: int) -> list[int]:
    if n < 2:
        return []
    sieve = bytearray([1]) * (n + 1)
    sieve[0] = sieve[1] = 0
    for i in range(2, int(n ** 0.5) + 1):
        if sieve[i]:
            sieve[i * i :: i] = bytearray(len(sieve[i * i :: i]))
    return [i for i, is_prime in enumerate(sieve) if is_prime]


if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 100
    primes = primes_up_to(n)
    print(f"Primes up to {n}: {len(primes)}")
    print(*primes)
