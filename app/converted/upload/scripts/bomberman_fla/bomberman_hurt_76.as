package bomberman_fla
{
    import flash.display.MovieClip;

    public dynamic class bomberman_hurt_76 extends MovieClip
    {

        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var itemBox:MovieClip;
        public var self:BombermanExt;
        public var xframe:String;
        public var projectile:*;

        public function bomberman_hurt_76()
        {
            super();
            addFrameScript(0, this.frame1, 8, this.frame9, 9, this.frame10, 10, this.frame11, 18, this.frame19, 19, this.frame20, 20, this.frame21, 28, this.frame29, 29, this.frame30, 30, this.frame31, 38, this.frame39, 39, this.frame40, 40, this.frame41, 49, this.frame50, 58, this.frame59, 59, this.frame60, 60, this.frame61, 66, this.frame67, 68, this.frame69, 69, this.frame70, 70, this.frame71, 78, this.frame79, 79, this.frame80);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as BombermanExt);
            this.xframe = "hurt1";
            if (parent && SSF2API.isReady() && this.self)
            {
                this.projectile = this.self.getGlobalVariable("bombCharge");
                if (this.projectile != null)
                {
                    this.projectile.destroy();
                };
                this.self.setGlobalVariable("bombCharge", null);
                this.self.setGlobalVariable("jab", false);
                this.self.setGlobalVariable("jab2", false);
            };
        }

        internal function frame9():*
        {
            this.xframe = "done1";
            stop();
        }

        internal function frame10():*
        {
            this.self.stancePlayFrame("done1");
        }

        internal function frame11():*
        {
            this.xframe = "hurt2";
            this.projectile = this.self.getGlobalVariable("bombCharge");
            if (this.projectile != null)
            {
                this.projectile.destroy();
            };
            this.self.setGlobalVariable("bombCharge", null);
            this.self.setGlobalVariable("jab", false);
            this.self.setGlobalVariable("jab2", false);
        }

        internal function frame19():*
        {
            this.xframe = "done2";
            stop();
        }

        internal function frame20():*
        {
            this.self.stancePlayFrame("done2");
        }

        internal function frame21():*
        {
            this.xframe = "hurt3";
            this.projectile = this.self.getGlobalVariable("bombCharge");
            if (this.projectile != null)
            {
                this.projectile.destroy();
            };
            this.self.setGlobalVariable("bombCharge", null);
            this.self.setGlobalVariable("jab", false);
            this.self.setGlobalVariable("jab2", false);
        }

        internal function frame29():*
        {
            this.xframe = "done3";
            stop();
        }

        internal function frame30():*
        {
            this.self.stancePlayFrame("done3");
        }

        internal function frame31():*
        {
            this.xframe = "downed";
        }

        internal function frame39():*
        {
            this.xframe = "downed";
            stop();
        }

        internal function frame40():*
        {
            this.self.stancePlayFrame("downed");
        }

        internal function frame41():*
        {
            this.xframe = "shock";
            stop();
        }

        internal function frame50():*
        {
            this.self.stancePlayFrame("shock");
        }

        internal function frame59():*
        {
            this.xframe = "ball";
            stop();
        }

        internal function frame60():*
        {
            this.self.stancePlayFrame("ball");
        }

        internal function frame61():*
        {
            this.xframe = "faint";
        }

        internal function frame67():*
        {
            this.self.attachEffect("effect_land");
            SSF2API.getCamera().shake(2);
            if (parent && SSF2API.isReady() && this.self)
            {
                if (this.self.getMetalStatus())
                {
                    this.self.playSound("metal_land_l");
                }
                else
                {
                    this.self.playSound("bomberman_landHeavy");
                };
            };
        }

        internal function frame69():*
        {
            this.xframe = "faintDone";
            stop();
        }

        internal function frame70():*
        {
            this.self.stancePlayFrame("faintDone");
        }

        internal function frame71():*
        {
            this.xframe = "spin";
        }

        internal function frame79():*
        {
            this.xframe = "spin";
            stop();
        }

        internal function frame80():*
        {
            this.self.stancePlayFrame("spin");
        }


    }
}

