// Most JNI: Kotlin <-> DemoDevice (wirtualne urządzenie TeklaPelletCAN w trybie demo: prawdziwy silnik i API z firmware).
#include <jni.h>
#include <string>
#include "demo_device.h"

using tpc::DemoDevice;
using tpc::HttpRequest;
using tpc::HttpResponse;

static std::string str(JNIEnv* env, jstring s) {
    if (!s) return std::string();
    const char* c = env->GetStringUTFChars(s, nullptr);
    std::string r(c ? c : "");
    if (c) env->ReleaseStringUTFChars(s, c);
    return r;
}

extern "C" {

JNIEXPORT jlong JNICALL Java_pl_gieoerzet_teklapelletcan_Native_create(JNIEnv* env, jclass, jstring fw) {
    return reinterpret_cast<jlong>(new DemoDevice(str(env, fw)));
}

JNIEXPORT void JNICALL Java_pl_gieoerzet_teklapelletcan_Native_destroy(JNIEnv*, jclass, jlong h) {
    delete reinterpret_cast<DemoDevice*>(h);
}

JNIEXPORT void JNICALL Java_pl_gieoerzet_teklapelletcan_Native_tick(JNIEnv*, jclass, jlong h) {
    if (h) reinterpret_cast<DemoDevice*>(h)->tick();
}

// Zwraca bajty: "<status>\n<content-type>\n<content-disposition>\n<ciało>" (ciało może zawierać dowolne znaki, w tym nowe linie).
JNIEXPORT jbyteArray JNICALL Java_pl_gieoerzet_teklapelletcan_Native_handle(JNIEnv* env, jclass, jlong h, jstring method, jstring path,
                                                                           jstring query, jstring authorization, jbyteArray body) {
    HttpRequest req;
    req.method = str(env, method);
    req.path = str(env, path);
    req.query = str(env, query);
    const std::string auth = str(env, authorization);
    if (!auth.empty()) req.headers["authorization"] = auth;
    if (body) {
        const jsize n = env->GetArrayLength(body);
        req.body.resize((size_t)n);
        if (n > 0) env->GetByteArrayRegion(body, 0, n, reinterpret_cast<jbyte*>(&req.body[0]));
    }
    HttpResponse r = h ? reinterpret_cast<DemoDevice*>(h)->handle(req) : HttpResponse();
    std::string disp;
    auto d = r.headers.find("Content-Disposition");
    if (d != r.headers.end()) disp = d->second;
    std::string out = std::to_string(r.status) + "\n" + r.ctype + "\n" + disp + "\n";
    out += r.body;
    jbyteArray res = env->NewByteArray((jsize)out.size());
    if (res) env->SetByteArrayRegion(res, 0, (jsize)out.size(), reinterpret_cast<const jbyte*>(out.data()));
    return res;
}

}  // extern "C"
