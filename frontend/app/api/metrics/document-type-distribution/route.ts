import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
  console.log('Backend URL:', process.env.NEXT_PUBLIC_BACKEND_URL);
  try {
    const { query } = await request.json();

    if (!query) {
      return NextResponse.json({ error: 'Query is required' }, { status: 400 });
    }

    // Call the general metrics API
    const response = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL}/run-sql`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ query }),
    });

    if (!response.ok) {
      const errorData = await response.json();
      return NextResponse.json({ error: errorData.error || 'Failed to execute query' }, { status: response.status });
    }

    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error('Error in document type distribution API:', error);
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 });
  }
} 