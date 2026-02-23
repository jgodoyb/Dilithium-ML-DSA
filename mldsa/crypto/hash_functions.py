# src/mldsa/crypto/hash_functions.py
import hashlib

class _XOFContext:
    """
    Contexto interno para manejar el estado incremental de Absorb y Squeeze.
    """
    def __init__(self, is_shake256=True):
        if is_shake256:
            self.xof = hashlib.shake_256()
        else:
            self.xof = hashlib.shake_128()
        self.offset = 0 # Rastrea cuántos bytes hemos "exprimido" ya

class H:
    """
    Wrapper para SHAKE256 según FIPS 204.
    """
    @staticmethod
    def digest(data: bytes, l: int) -> bytes:
        """H(str, l) = SHAKE256(str, 8l). Devuelve l bytes."""
        return hashlib.shake_256(data).digest(l)

    @staticmethod
    def Init() -> _XOFContext:
        """ctx <- H.Init()"""
        return _XOFContext(is_shake256=True)

    @staticmethod
    def Absorb(ctx: _XOFContext, data: bytes) -> _XOFContext:
        """ctx <- H.Absorb(ctx, str)"""
        ctx.xof.update(data)
        return ctx

    @staticmethod
    def Squeeze(ctx: _XOFContext, l: int) -> tuple[_XOFContext, bytes]:
        """
        (ctx, out) <- H.Squeeze(ctx, l)
        Extrae l bytes del flujo continuo.
        """
        # Pedimos el total de bytes generados hasta ahora + los nuevos que queremos
        total_needed = ctx.offset + l
        full_output = ctx.xof.digest(total_needed)
        # Recortamos solo la parte nueva que no habíamos leído
        out = full_output[ctx.offset : total_needed]
        ctx.offset += l
        return ctx, out

class G:
    """
    Wrapper para SHAKE128 según FIPS 204.
    """
    @staticmethod
    def digest(data: bytes, l: int) -> bytes:
        """G(str, l) = SHAKE128(str, 8l). Devuelve l bytes."""
        return hashlib.shake_128(data).digest(l)

    @staticmethod
    def Init() -> _XOFContext:
        """ctx <- G.Init()"""
        return _XOFContext(is_shake256=False)

    @staticmethod
    def Absorb(ctx: _XOFContext, data: bytes) -> _XOFContext:
        """ctx <- G.Absorb(ctx, str)"""
        ctx.xof.update(data)
        return ctx

    @staticmethod
    def Squeeze(ctx: _XOFContext, l: int) -> tuple[_XOFContext, bytes]:
        """(ctx, out) <- G.Squeeze(ctx, l)"""
        total_needed = ctx.offset + l
        full_output = ctx.xof.digest(total_needed)
        out = full_output[ctx.offset : total_needed]
        ctx.offset += l
        return ctx, out