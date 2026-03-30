package ssf2intro_beta_fla
{
    import flash.display.MovieClip;

    public dynamic class minuteHand_195 extends MovieClip
    {

        public var myDate:*;
        public var hour:Number;

        public function minuteHand_195()
        {
            super();
            addFrameScript(0, this.frame1, 2, this.frame3, 4, this.frame5, 6, this.frame7, 8, this.frame9, 10, this.frame11, 12, this.frame13, 14, this.frame15, 16, this.frame17, 18, this.frame19, 20, this.frame21, 22, this.frame23, 24, this.frame25);
        }

        internal function frame1():*
        {
            this.myDate = new Date();
            this.hour = (this.myDate.getMinutes() + 1);
            gotoAndStop(int((this.hour * 0.4)));
        }

        internal function frame3():*
        {
            gotoAndStop(2);
        }

        internal function frame5():*
        {
            gotoAndStop(4);
        }

        internal function frame7():*
        {
            gotoAndStop(6);
        }

        internal function frame9():*
        {
            gotoAndStop(8);
        }

        internal function frame11():*
        {
            gotoAndStop(10);
        }

        internal function frame13():*
        {
            gotoAndStop(12);
        }

        internal function frame15():*
        {
            gotoAndStop(14);
        }

        internal function frame17():*
        {
            gotoAndStop(16);
        }

        internal function frame19():*
        {
            gotoAndStop(18);
        }

        internal function frame21():*
        {
            gotoAndStop(20);
        }

        internal function frame23():*
        {
            gotoAndStop(22);
        }

        internal function frame25():*
        {
            gotoAndStop(24);
        }


    }
}

