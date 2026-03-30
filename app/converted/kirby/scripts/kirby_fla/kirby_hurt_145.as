package kirby_fla
{
    import flash.display.MovieClip;

    public dynamic class kirby_hurt_145 extends MovieClip
    {

        public var hatBox:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var hitBox4:MovieClip;
        public var itemBox:MovieClip;
        public var self:KirbyExt;
        public var xframe:String;

        public function kirby_hurt_145()
        {
            super();
            addFrameScript(0, this.frame1, 8, this.frame9, 9, this.frame10, 10, this.frame11, 18, this.frame19, 19, this.frame20, 20, this.frame21, 28, this.frame29, 29, this.frame30, 30, this.frame31, 38, this.frame39, 39, this.frame40, 40, this.frame41, 48, this.frame49, 49, this.frame50, 50, this.frame51, 60, this.frame61, 61, this.frame62, 68, this.frame69, 69, this.frame70, 70, this.frame71, 79, this.frame80, 88, this.frame89, 89, this.frame90, 90, this.frame91, 96, this.frame97, 98, this.frame99, 99, this.frame100, 100, this.frame101, 108, this.frame109, 109, this.frame110);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as KirbyExt);
            this.xframe = "hurt1";
        }

        internal function frame9():*
        {
            this.xframe = "done1";
            stop();
        }

        internal function frame10():*
        {
            gotoAndStop("done1");
        }

        internal function frame11():*
        {
            this.xframe = "hurt2";
        }

        internal function frame19():*
        {
            this.xframe = "done2";
            stop();
        }

        internal function frame20():*
        {
            gotoAndStop("done2");
        }

        internal function frame21():*
        {
            this.xframe = "hurt3";
        }

        internal function frame29():*
        {
            this.xframe = "done3";
            stop();
        }

        internal function frame30():*
        {
            gotoAndStop("done3");
        }

        internal function frame31():*
        {
            this.xframe = "hurt4";
        }

        internal function frame39():*
        {
            this.xframe = "done4";
            stop();
        }

        internal function frame40():*
        {
            gotoAndStop("done4");
        }

        internal function frame41():*
        {
            this.xframe = "hurt5";
        }

        internal function frame49():*
        {
            this.xframe = "done5";
            stop();
        }

        internal function frame50():*
        {
            gotoAndStop("done5");
        }

        internal function frame51():*
        {
            this.xframe = "fathurt1";
            stop();
        }

        internal function frame61():*
        {
            gotoAndStop("done5");
        }

        internal function frame62():*
        {
            this.xframe = "downed";
        }

        internal function frame69():*
        {
            this.xframe = "downed";
            stop();
        }

        internal function frame70():*
        {
            this.self.stancePlayFrame("downed");
        }

        internal function frame71():*
        {
            this.xframe = "shock";
            stop();
        }

        internal function frame80():*
        {
            gotoAndStop("shock");
        }

        internal function frame89():*
        {
            this.xframe = "ball";
            stop();
        }

        internal function frame90():*
        {
            this.self.stancePlayFrame("ball");
        }

        internal function frame91():*
        {
            this.xframe = "faint";
        }

        internal function frame97():*
        {
            this.self.setGlobalVariable("canStartRise", true);
            this.self.attachEffect("effect_land");
            if (this.self.getMetalStatus())
            {
                this.self.playSound("metal_land_s");
            }
            else
            {
                this.self.playSound("kirby_land1");
            };
        }

        internal function frame99():*
        {
            this.xframe = "faintDone";
            stop();
        }

        internal function frame100():*
        {
            this.self.stancePlayFrame("faintDone");
        }

        internal function frame101():*
        {
            this.xframe = "spin";
        }

        internal function frame109():*
        {
            this.xframe = "spin";
            stop();
        }

        internal function frame110():*
        {
            this.self.stancePlayFrame("spin");
        }


    }
}

