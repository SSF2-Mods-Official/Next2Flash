package fox_fla
{
    import flash.display.MovieClip;

    public dynamic class fox_smashS_39 extends MovieClip
    {

        public var attackBox:MovieClip;
        public var attackBox2:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var hitBox4:MovieClip;
        public var itemBox:MovieClip;
        public var self:FoxExt;
        public var xframe:String;

        public function fox_smashS_39()
        {
            super();
            addFrameScript(0, this.frame1, 4, this.frame5, 44, this.frame45, 45, this.frame46, 47, this.frame48, 48, this.frame49, 51, this.frame52, 52, this.frame53, 59, this.frame60, 66, this.frame67);
        }

        public function effects():void
        {
            this.self.attachEffect("global_dust_heavy", {
                "x":this.self.flipX(8),
                "y":3,
                "scaleX":-0.5,
                "scaleY":-0.5
            });
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as FoxExt);
        }

        internal function frame5():*
        {
            this.xframe = "charging";
            this.self.createTimer(4, -1, this.effects);
        }

        internal function frame45():*
        {
            this.self.stancePlayFrame("charging");
        }

        internal function frame46():*
        {
            this.xframe = "attack";
            this.self.destroyTimer(this.effects);
            this.self.setXSpeed(6.2, false);
            this.self.playVoiceSound(1);
            this.self.playAttackSound(2);
        }

        internal function frame48():*
        {
            this.self.attachEffect("global_dust_heavy", {
                "scaleX":0.7,
                "scaleY":0.55
            });
            this.self.setXSpeed(13.5, false);
        }

        internal function frame49():*
        {
            this.self.playAttackSound(1);
            this.self.playAttackSound(3);
        }

        internal function frame52():*
        {
            this.self.updateAttackBoxStats(1, {"damage":11});
        }

        internal function frame53():*
        {
            this.self.updateAttackStats({"air_ease":-1});
        }

        internal function frame60():*
        {
            if (this.self.getMetalStatus())
            {
                this.self.playSound("metal_land_s");
            }
            else
            {
                this.self.playSound("fox_landLight");
            };
        }

        internal function frame67():*
        {
            this.self.endAttack();
        }


    }
}

