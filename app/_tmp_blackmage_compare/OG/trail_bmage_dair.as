package
{
    import flash.display.MovieClip;

    public dynamic class trail_bmage_dair extends MovieClip
    {

        public function trail_bmage_dair()
        {
            super();
            addFrameScript(8, this.frame9);
        }

        internal function frame9():*
        {
            stop();
            if (parent)
            {
                parent.removeChild(this);
            };
        }


    }
}

