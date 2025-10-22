"use client"
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { toast } from "sonner";

export default function Home() {
  return (
    <div className="flex min-h-screen items-center justify-center bg-background text-foreground">
      <Card className="p-6 space-y-4">
        <CardContent className="text-center space-y-4">
          <h1 className="text-2xl font-semibold">PantryPal</h1>
          <Button
            size="lg"
            onClick={() => toast.success("shadcn + Sonner are wired!")}
          >
            Test UI & Toast
          </Button>
        </CardContent>
      </Card>
    </div>
  );
}
