package pl.gieoerzet.teklapelletcan

/** Biblioteka natywna z rdzeniem firmware (silnik + API + wirtualny kocioł) – to samo, co działa na urządzeniu. */
object Native {
    init { System.loadLibrary("tpc_demo") }

    @JvmStatic external fun create(fw: String): Long
    @JvmStatic external fun destroy(h: Long)
    @JvmStatic external fun tick(h: Long)

    /** Zwraca "<status>\n<content-type>\n<content-disposition>\n<ciało>". */
    @JvmStatic external fun handle(h: Long, method: String, path: String, query: String, authorization: String, body: ByteArray): ByteArray
}
