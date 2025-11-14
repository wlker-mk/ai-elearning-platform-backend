-- CreateExtension
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- CreateExtension
CREATE EXTENSION IF NOT EXISTS "unaccent";

-- CreateTable
CREATE TABLE "course_views" (
    "id" TEXT NOT NULL,
    "courseId" TEXT NOT NULL,
    "userId" TEXT,
    "ipAddress" TEXT,
    "userAgent" TEXT,
    "country" TEXT,
    "city" TEXT,
    "referrer" TEXT,
    "source" TEXT,
    "viewedAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "course_views_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "video_analytics" (
    "id" TEXT NOT NULL,
    "lessonId" TEXT NOT NULL,
    "studentId" TEXT NOT NULL,
    "totalWatchTime" INTEGER NOT NULL DEFAULT 0,
    "completionRate" DOUBLE PRECISION NOT NULL DEFAULT 0,
    "pauseCount" INTEGER NOT NULL DEFAULT 0,
    "rewindCount" INTEGER NOT NULL DEFAULT 0,
    "speedChanges" INTEGER NOT NULL DEFAULT 0,
    "avgQuality" TEXT,
    "lastPosition" INTEGER NOT NULL DEFAULT 0,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updatedAt" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "video_analytics_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "search_logs" (
    "id" TEXT NOT NULL,
    "query" TEXT NOT NULL,
    "userId" TEXT,
    "ipAddress" TEXT,
    "resultsCount" INTEGER NOT NULL DEFAULT 0,
    "clickedResult" TEXT,
    "searchedAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "search_logs_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "user_activity" (
    "id" TEXT NOT NULL,
    "userId" TEXT NOT NULL,
    "eventType" TEXT NOT NULL,
    "metadata" JSONB,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "user_activity_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "revenue_reports" (
    "id" TEXT NOT NULL,
    "date" DATE NOT NULL,
    "totalRevenue" DOUBLE PRECISION NOT NULL DEFAULT 0,
    "totalOrders" INTEGER NOT NULL DEFAULT 0,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "revenue_reports_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "course_analytics" (
    "id" TEXT NOT NULL,
    "courseId" TEXT NOT NULL,
    "date" DATE NOT NULL,
    "views" INTEGER NOT NULL DEFAULT 0,
    "enrollments" INTEGER NOT NULL DEFAULT 0,
    "completions" INTEGER NOT NULL DEFAULT 0,
    "avgRating" DOUBLE PRECISION,
    "createdAt" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "course_analytics_pkey" PRIMARY KEY ("id")
);

-- CreateIndex
CREATE INDEX "course_views_courseId_viewedAt_idx" ON "course_views"("courseId", "viewedAt");

-- CreateIndex
CREATE INDEX "course_views_userId_viewedAt_idx" ON "course_views"("userId", "viewedAt");

-- CreateIndex
CREATE INDEX "video_analytics_studentId_lessonId_idx" ON "video_analytics"("studentId", "lessonId");

-- CreateIndex
CREATE UNIQUE INDEX "video_analytics_lessonId_studentId_key" ON "video_analytics"("lessonId", "studentId");

-- CreateIndex
CREATE INDEX "search_logs_query_searchedAt_idx" ON "search_logs"("query", "searchedAt");

-- CreateIndex
CREATE INDEX "search_logs_userId_searchedAt_idx" ON "search_logs"("userId", "searchedAt");

-- CreateIndex
CREATE INDEX "user_activity_userId_eventType_createdAt_idx" ON "user_activity"("userId", "eventType", "createdAt");

-- CreateIndex
CREATE UNIQUE INDEX "revenue_reports_date_key" ON "revenue_reports"("date");

-- CreateIndex
CREATE UNIQUE INDEX "course_analytics_courseId_date_key" ON "course_analytics"("courseId", "date");
