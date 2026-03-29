package
{
    import flash.display.MovieClip;

    public dynamic class raptorboost_ground_hit extends MovieClip
    {

        public function raptorboost_ground_hit()
        {
            super();
            addFrameScript(9, this.frame10);
        }

        internal function frame10():*
        {
            stop();
            if ((root != null) && (parent != null))
            {
                parent.removeChild(this);
            };
        }


    }
}

