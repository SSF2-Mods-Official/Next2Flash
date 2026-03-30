package simon_fla
{
    import flash.display.MovieClip;

    public dynamic class FinalSmashCoffinMask_114 extends MovieClip
    {

        public var charContainer:MovieClip;

        public function FinalSmashCoffinMask_114()
        {
            super();
            addFrameScript(3, this.frame4, 4, this.frame5);
        }

        internal function frame4():*
        {
            stop();
        }

        internal function frame5():*
        {
            gotoAndStop((currentFrame - 1));
        }


    }
}

