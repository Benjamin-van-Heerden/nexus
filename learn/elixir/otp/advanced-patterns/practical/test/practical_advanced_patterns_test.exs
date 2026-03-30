defmodule PracticalAdvancedPatternsTest do
  use ExUnit.Case
  doctest PracticalAdvancedPatterns

  test "greets the world" do
    assert PracticalAdvancedPatterns.hello() == :world
  end
end
