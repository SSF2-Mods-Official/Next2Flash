package gameandwatch_fla
{
    import flash.display.MovieClip;

    public dynamic class food_122 extends MovieClip
    {

        public function food_122()
        {
            super();
            addFrameScript(0, this.frame1, 1, this.frame2, 2, this.frame3, 3, this.frame4, 4, this.frame5, 5, this.frame6);
        }

        internal function frame1():*
        {
            stop();
        }

        internal function frame2():*
        {
            this.gotoAndStop(1);
        }

        internal function frame3():*
        {
            stop();
        }

        internal function frame4():*
        {
            this.gotoAndStop(3);
        }

        internal function frame5():*
        {
            stop();
        }

        internal function frame6():*
        {
            this.gotoAndStop(5);
        }


    }
}

