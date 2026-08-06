package org.example.patterns;
public class InventoryIspTest {
    public static void main(String[] args) {
        InventoryStore st = new InventoryStore();
        st.write("x");
        if (!InventoryIspClient.mirror(st).equals("inventory:x")) throw new AssertionError();
        System.out.println("ok");
    }
}
