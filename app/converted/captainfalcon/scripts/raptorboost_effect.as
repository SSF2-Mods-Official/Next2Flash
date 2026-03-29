package
{
    import flash.display.MovieClip;

    public dynamic class raptorboost_effect extends MovieClip
    {

        public function raptorboost_effect()
        {
            super();
            addFrameScript(8, this.frame9);
        }

        internal function frame9():*
        {
            stop();
            if ((root != null) && (parent != null))
            {
                parent.removeChild(this);
            };
        }


    }
}

