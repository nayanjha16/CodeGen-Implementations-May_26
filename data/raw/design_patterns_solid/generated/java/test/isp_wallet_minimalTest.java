package org.example.patterns;
public class WalletIspTest {
    public static void main(String[] args) {
        WalletStore st = new WalletStore();
        st.write("x");
        if (!WalletIspClient.mirror(st).equals("wallet:x")) throw new AssertionError();
        System.out.println("ok");
    }
}
