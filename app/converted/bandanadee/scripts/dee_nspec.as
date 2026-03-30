package
{
    import flash.display.MovieClip;

    public dynamic class dee_nspec extends MovieClip
    {

        public var stance:MovieClip;
        public var xframe:*;

        public function dee_nspec()
        {
            super();
            addFrameScript(0, this.frame1);
        }

        internal function frame1():*
        {
            this.xframe = "attack_idle";
            stop();
        }


    }
}

