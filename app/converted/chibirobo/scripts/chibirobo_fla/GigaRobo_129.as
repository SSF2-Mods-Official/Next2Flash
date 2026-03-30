package chibirobo_fla
{
    import flash.display.MovieClip;

    public dynamic class GigaRobo_129 extends MovieClip
    {

        public var attackBox:MovieClip;
        public var attackBox2:MovieClip;
        public var camBox:MovieClip;
        public var loop:*;
        public var self:*;
        public var audio:Number;
        public var playsound:Number;
        public var character:*;

        public function GigaRobo_129()
        {
            super();
            addFrameScript(0, this.frame1, 2, this.frame3, 3, this.frame4, 24, this.frame25, 36, this.frame37, 50, this.frame51, 51, this.frame52, 65, this.frame66);
        }

        public function toLand(_arg_1:*=null):void
        {
            this.self.stancePlayFrame("land");
        }

        public function gigaVoice():void
        {
            this.playsound = SSF2API.random();
            if ((this.playsound > 0) && (this.playsound <= 0.14) && (this.audio != 1))
            {
                this.self.playSound("giga_voice1", true);
                this.audio = 1;
            };
            if ((this.playsound > 0.14) && (this.playsound <= 0.28) && (this.audio != 2))
            {
                this.self.playSound("giga_voice2", true);
                this.audio = 2;
            };
            if ((this.playsound > 0.28) && (this.playsound <= 0.42) && (this.audio != 3))
            {
                this.self.playSound("giga_voice3", true);
                this.audio = 3;
            };
            if ((this.playsound > 0.42) && (this.playsound <= 56) && (this.audio != 4))
            {
                this.self.playSound("giga_voice4", true);
                this.audio = 4;
            };
            if ((this.playsound > 0.56) && (this.playsound <= 70) && (this.audio != 5))
            {
                this.self.playSound("giga_voice5", true);
                this.audio = 5;
            };
            if ((this.playsound > 0.7) && (this.playsound <= 84) && (this.audio != 6))
            {
                this.self.playSound("giga_voice6", true);
                this.audio = 6;
            };
            if ((this.playsound > 0.84) && (this.playsound <= 1) && (this.audio != 7))
            {
                this.self.playSound("giga_voice7", true);
                this.audio = 7;
            };
        }

        public function up(_arg_1:*=null):void
        {
            this.self.setYSpeed((this.self.getYSpeed() * 2));
        }

        internal function frame1():*
        {
            this.loop = 0;
            this.self = SSF2API.getProjectile(this);
            if (SSF2API.isReady() && this.self)
            {
                this.character = this.self.getOwner();
                this.self.addEventListener(SSF2Event.GROUND_TOUCH, this.toLand);
                this.self.addToCamera();
            };
        }

        internal function frame3():*
        {
            this.self.stancePlayFrame("fall");
        }

        internal function frame4():*
        {
            this.self.playSound("giga_step");
        }

        internal function frame25():*
        {
            this.gigaVoice();
        }

        internal function frame37():*
        {
            var _local_1:* = __activation__;
            this.self.refreshAttackID();
            this.self.createTimer(2, 5, function ():*
            {
                SSF2API.getCamera().shake(10);
            });
            this.self.playSound("giga_step");
        }

        internal function frame51():*
        {
            if (this.loop < 10)
            {
                this.loop++;
                if (SSF2API.random() > 0.65)
                {
                    this.self.flip();
                };
                this.self.stancePlayFrame("idle");
            };
        }

        internal function frame52():*
        {
            this.self.setYSpeed(-5);
            this.self.createTimer(1, -1, this.up);
            this.self.removeFromCamera();
            this.self.playSound("giga_exit");
        }

        internal function frame66():*
        {
            this.self.destroy();
        }


    }
}

