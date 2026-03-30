package simon_fla
{
    import flash.display.MovieClip;

    public dynamic class NSpecial_31 extends MovieClip
    {

        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var hitBox4:MovieClip;
        public var itemBox:MovieClip;
        public var self:SimonExt;

        public function NSpecial_31()
        {
            super();
            addFrameScript(0, this.frame1, 13, this.frame14, 15, this.frame16, 29, this.frame30);
        }

        public function removeControl(_arg_1:*=null):*
        {
            this.self.updateAttackStats({"allowControl":false});
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as SimonExt);
            if (this.self && SSF2API.isReady() && parent)
            {
                this.self.addEventListener(SSF2Event.GROUND_TOUCH, this.removeControl);
            };
        }

        internal function frame14():*
        {
            this.self.attachEffect("global_spark", {
                "scaleX":0.6,
                "scaleY":0.6,
                "x":this.self.flipX(10),
                "y":-20
            });
        }

        internal function frame16():*
        {
            this.self.fireProjectile("axe", 20, -30);
            this.self.playAttackSound(1);
            this.self.playVoiceSound(1);
        }

        internal function frame30():*
        {
            this.self.endAttack();
        }


    }
}

