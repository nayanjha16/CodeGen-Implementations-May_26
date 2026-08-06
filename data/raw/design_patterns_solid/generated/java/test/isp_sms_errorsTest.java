package org.example.patterns;
public class SmsIspTest {
    public static void main(String[] args) {
        SmsStore st = new SmsStore();
        st.write("x");
        if (!SmsIspClient.mirror(st).equals("sms:x")) throw new AssertionError();
        System.out.println("ok");
    }
}
