"use client";

import React from "react";
import { Card } from "@/components/ui/card";
import { Bot, User, Brain, Wrench, AlertCircle } from "lucide-react";

interface Message {
  id: string;
  type: "user" | "agent" | "thought" | "tool" | "error";
  content: string;
  timestamp: Date;
}

interface MessageBubbleProps {
  message: Message;
}

export function MessageBubble({ message }: MessageBubbleProps) {
  const getIcon = () => {
    switch (message.type) {
      case "user":
        return <User className="h-5 w-5 text-blue-600" />;
      case "agent":
        return <Bot className="h-5 w-5 text-green-600" />;
      case "thought":
        return <Brain className="h-5 w-5 text-purple-600" />;
      case "tool":
        return <Wrench className="h-5 w-5 text-orange-600" />;
      case "error":
        return <AlertCircle className="h-5 w-5 text-red-600" />;
      default:
        return <Bot className="h-5 w-5" />;
    }
  };

  const getBgColor = () => {
    switch (message.type) {
      case "user":
        return "bg-blue-50 border-blue-200";
      case "agent":
        return "bg-green-50 border-green-200";
      case "thought":
        return "bg-purple-50 border-purple-200";
      case "tool":
        return "bg-orange-50 border-orange-200";
      case "error":
        return "bg-red-50 border-red-200";
      default:
        return "bg-gray-50 border-gray-200";
    }
  };

  const getLabel = () => {
    switch (message.type) {
      case "user":
        return "You";
      case "agent":
        return "Agent";
      case "thought":
        return "Agent Thinking";
      case "tool":
        return "Tool Execution";
      case "error":
        return "Error";
      default:
        return "Message";
    }
  };

  const formatTime = (date: Date) => {
    return date.toLocaleTimeString("en-US", {
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  return (
    <Card className={`p-4 ${getBgColor()}`}>
      <div className="flex items-start gap-3">
        <div className="mt-1">{getIcon()}</div>
        <div className="flex-1 min-w-0">
          <div className="flex items-center justify-between mb-2">
            <span className="font-semibold text-sm">{getLabel()}</span>
            <span className="text-xs text-muted-foreground">
              {formatTime(message.timestamp)}
            </span>
          </div>
          <div className="prose prose-sm max-w-none dark:prose-invert">
            <p className="whitespace-pre-wrap break-words m-0">
              {message.content}
            </p>
          </div>
        </div>
      </div>
    </Card>
  );
}
