package
{
    import flash.display.MovieClip;

    public dynamic class dedede_jump_star extends MovieClip
    {

        public var stance:MovieClip;

        public function dedede_jump_star()
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

