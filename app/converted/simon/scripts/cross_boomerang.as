package
{
    import flash.display.MovieClip;

    public dynamic class cross_boomerang extends MovieClip
    {

        public var stance:MovieClip;
        public var xframe:*;

        public function cross_boomerang()
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

