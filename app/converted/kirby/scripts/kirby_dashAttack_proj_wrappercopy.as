package
{
    import flash.display.MovieClip;

    public dynamic class kirby_dashAttack_proj_wrappercopy extends MovieClip
    {

        public var stance:kirby_afterimage;

        public function kirby_dashAttack_proj_wrappercopy()
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

