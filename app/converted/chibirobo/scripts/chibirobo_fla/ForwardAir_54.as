package chibirobo_fla
{
    import flash.display.MovieClip;

    public dynamic class ForwardAir_54 extends MovieClip
    {

        public var attackBox:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var hitBox4:MovieClip;
        public var hitBox5:MovieClip;
        public var itemBox:MovieClip;
        public var self:ChibiExt;
        public var playsound:*;

        public function ForwardAir_54()
        {
            super();
            addFrameScript(0, this.frame1, 2, this.frame3, 5, this.frame6, 7, this.frame8, 8, this.frame9, 13, this.frame14, 18, this.frame19, 19, this.frame20, 24, this.frame25);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as ChibiExt);
            if (parent && SSF2API.isReady() && this.self)
            {
                this.self.setLandingLag(false);
            };
        }

        internal function frame3():*
        {
            this.self.setLandingLag(true);
        }

        internal function frame6():*
        {
            if (!this.self.getMetalStatus())
            {
                this.playsound = SSF2API.random();
                if ((this.playsound > 0) && (this.playsound <= 0.25))
                {
                    this.self.playSound("chibi_Spoon1");
                };
                if ((this.playsound > 0.25) && (this.playsound <= 0.5))
                {
                    this.self.playSound("chibi_Spoon2");
                };
                if ((this.playsound > 0.5) && (this.playsound <= 0.75))
                {
                    this.self.playSound("chibi_Spoon3");
                };
                if ((this.playsound > 0.75) && (this.playsound <= 1))
                {
                    this.self.playSound("chibi_Spoon4");
                };
            };
        }

        internal function frame8():*
        {
            this.self.updateAttackBoxStats(1, {"direction":70});
        }

        internal function frame9():*
        {
            this.self.updateAttackBoxStats(1, {"direction":85});
        }

        internal function frame14():*
        {
            this.self.setLandingLag(false);
        }

        internal function frame19():*
        {
            this.self.endAttack();
        }

        internal function frame20():*
        {
            SSF2API.print("continue");
            SSF2API.getCamera().shake(2);
            if (this.self.getMetalStatus())
            {
                this.self.playSound("metal_land_s");
            }
            else
            {
                this.self.playSound("chibi_DStep");
            };
        }

        internal function frame25():*
        {
            this.self.endAttack();
        }


    }
}

