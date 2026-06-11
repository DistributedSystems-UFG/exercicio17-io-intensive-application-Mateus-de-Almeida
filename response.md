============================================================
RESULTADO COMPARATIVO (vazão media em req/s)
============================================================
Versão                      Vazão (req/s)
------------------------------------------
Single-threaded                 22,654.52
Thread-per-request              42,507.76
Thread-pool                     44,252.79
------------------------------------------
Melhor: Thread-pool (44,252.79 req/s)
Pior:   Single-threaded (22,654.52 req/s)
------------------------------------------

Em single thread, apenas um cliente pode ser atendido por vez. Em thread-per-request e thread-pool, mais de um cliente pode ser atendido simultaneamente, logo, como há mais de um núcleo de cpu disponível e a paralelização é viável, já era esperado que single thread teria a menor vazão. Quanto ao fato de thread-poll ter tido maior vazão quando comparado a thread-per-request, se deve á:
    * A quantidade de threads simultâneas alocadas para o thread-pool aproveitou todas as threads disponíveis no sistema, dessa forma, simultaneamente, tanto o thread-pool quanto o thread-per-request tentavam manter o mesmo número de threads ativas por vez.
    * O modelo thread-pool elimina o custo de criação e destruição de threads sob demanda. Enquanto a abordagem thread-per-request aloca recursos do sistema operacional a cada nova conexão e os descarta logo em seguida, o pool de threads reutiliza um conjunto fixo de threads previamente instanciadas. Isso reduz o overhead de gerenciamento do sistema operacional e evita a degradação de desempenho causada pelo excesso de trocas de contexto (destruir e criar nova thread), resultando em uma maior eficiência e estabilidade na vazão de requisições.