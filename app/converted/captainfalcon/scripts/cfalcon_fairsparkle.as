package
{
    import flash.display.MovieClip;

    public dynamic class cfalcon_fairsparkle extends MovieClip
    {

        public function cfalcon_fairsparkle()
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

