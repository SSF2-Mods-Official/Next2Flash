package
{
    import flash.display.MovieClip;

    public dynamic class dee_finalsmash extends MovieClip
    {

        public var stance:deeFinalSmashProjectile;

        public function dee_finalsmash()
        {
            super();
            addFrameScript(0, this.frame1);
        }

        internal function frame1():*
        {
            stop();
        }


    }
}

