package
{
    import flash.display.MovieClip;

    public dynamic class jab_whip extends MovieClip
    {

        public var stance:MovieClip;
        public var xframe:*;

        public function jab_whip()
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

