import { Card, CardContent } from "@/components/ui/card";

export default function Page() {
  return (
    <div className="grid gap-4">
      <h1 className="text-2xl font-semibold">Dashboard</h1>

      <section className="grid grid-cols-1 gap-4 md:grid-cols-3">
        <Card>
          <CardContent className="p-4">
            <div className="text-sm text-muted-foreground">Total Items</div>
            <div className="text-2xl font-semibold">—</div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <div className="text-sm text-muted-foreground">Pending Approvals</div>
            <div className="text-2xl font-semibold">—</div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <div className="text-sm text-muted-foreground">Open Requests</div>
            <div className="text-2xl font-semibold">—</div>
          </CardContent>
        </Card>
      </section>
    </div>
  );
}
