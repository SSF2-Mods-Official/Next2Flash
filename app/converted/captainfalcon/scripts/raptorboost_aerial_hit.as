package
{
    import flash.display.MovieClip;

    public dynamic class raptorboost_aerial_hit extends MovieClip
    {

        public function raptorboost_aerial_hit()
        {
            super();
            addFrameScript(7, this.frame8);
        }

        internal function frame8():*
        {
            stop();
            if ((root != null) && (parent != null))
            {
                parent.removeChild(this);
            };
        }


    }
}

