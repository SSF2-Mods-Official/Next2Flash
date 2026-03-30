package
{
    import flash.display.MovieClip;

    public dynamic class axe extends MovieClip
    {

        public var stance:MovieClip;
        public var xframe:*;

        public function axe()
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

