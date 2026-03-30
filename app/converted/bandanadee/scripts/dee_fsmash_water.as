package
{
    import flash.display.MovieClip;

    public dynamic class dee_fsmash_water extends MovieClip
    {

        public function dee_fsmash_water()
        {
            super();
            addFrameScript(11, this.frame12);
        }

        internal function frame12():*
        {
            stop();
            if (parent)
            {
                parent.removeChild(this);
            };
        }


    }
}

