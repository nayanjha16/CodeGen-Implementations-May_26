package org.example.patterns;
public class LoggingIspTest {
    public static void main(String[] args) {
        LoggingStore st = new LoggingStore();
        st.write("x");
        if (!LoggingIspClient.mirror(st).equals("logging:x")) throw new AssertionError();
        System.out.println("ok");
    }
}
