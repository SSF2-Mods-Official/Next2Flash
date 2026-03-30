package
{
    import flash.display.MovieClip;

    public dynamic class trail_lucario_ftilt extends MovieClip
    {

        public function trail_lucario_ftilt()
        {
            super();
            addFrameScript(4, this.frame5);
        }

        internal function frame5():*
        {
            if (parent)
            {
                parent.removeChild(this);
            };
        }


    }
}

