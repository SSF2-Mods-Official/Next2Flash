package
{
    import flash.display.MovieClip;

    public dynamic class trail_lucario_utilt extends MovieClip
    {

        public function trail_lucario_utilt()
        {
            super();
            addFrameScript(7, this.frame8);
        }

        internal function frame8():*
        {
            if (parent)
            {
                parent.removeChild(this);
            };
        }


    }
}

