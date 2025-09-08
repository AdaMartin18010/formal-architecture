---- MODULE AsyncSyncPart1 ----
EXTENDS Naturals, Sequences

(* --algorithm AsyncSync
variables ch = << >>; \* 消息通道（队列）
variables bufCap \in 0..2; \* 缓冲区容量占位

process Producer = "P"
begin
  P1: while TRUE do
        if Len(ch) < bufCap then
          ch := Append(ch, "msg");
        end if;
      end while;
end process;

process Consumer = "C"
begin
  C1: while TRUE do
        if Len(ch) > 0 then
          ch := Tail(ch);
        end if;
      end while;
end process;

end algorithm; *)

\* 不变式占位：缓冲区不溢出
Inv == Len(ch) <= bufCap

====
