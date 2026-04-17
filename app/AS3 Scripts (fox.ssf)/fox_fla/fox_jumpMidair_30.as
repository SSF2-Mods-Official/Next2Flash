// Decompiled by AS3 Sorcerer 6.20
// www.as3sorcerer.com

//fox_fla.fox_jumpMidair_30

package fox_fla
{
    import flash.display.MovieClip;
    import flash.display.*;
    import flash.geom.*;
    import flash.events.*;
    import flash.media.*;
    import flash.filters.*;
    import flash.utils.*;
    import adobe.utils.*;
    import flash.accessibility.*;
    import flash.desktop.*;
    import flash.errors.*;
    import flash.external.*;
    import flash.globalization.*;
    import flash.net.*;
    import flash.net.drm.*;
    import flash.printing.*;
    import flash.profiler.*;
    import flash.sampler.*;
    import flash.sensors.*;
    import flash.system.*;
    import flash.text.*;
    import flash.text.ime.*;
    import flash.text.engine.*;
    import flash.ui.*;
    import flash.xml.*;

    public dynamic class fox_jumpMidair_30 extends MovieClip 
    {

        public var hand:MovieClip;
        public var hitBox:MovieClip;
        public var hitBox2:MovieClip;
        public var hitBox3:MovieClip;
        public var hitBox4:MovieClip;
        public var itemBox:MovieClip;
        public var self:FoxExt;

        public function fox_jumpMidair_30()
        {
            addFrameScript(0, this.frame1, 5, this.frame6, 11, this.frame12, 18, this.frame19);
        }

        internal function frame1():*
        {
            this.self = (SSF2API.getCharacter(this) as FoxExt);
            if (((SSF2API.isReady()) && (this.self)))
            {
                this.self.prevAnim = false;
                if (((this.self.getGlobalVariable("screwAttackOn")) && (this.self.getMidairJumpCount() < 2)))
                {
                    this.self.forceAttack("item_screw");
                }
                else
                {
                    if (((this.self.getGlobalVariable("sonicShieldFiredash")) && ((this.self.getControls().LEFT) || (this.self.getControls().RIGHT))))
                    {
                        this.self.forceAttack("item_firedash");
                    }
                    else
                    {
                        if (((this.self.getGlobalVariable("sonicShieldBubbleBounce")) && (this.self.getControls().DOWN)))
                        {
                            this.self.forceAttack("item_bubblebounce");
                        }
                        else
                        {
                            this.self.playSound("fox_jump02");
                        };
                    };
                };
            };
        }

        internal function frame6():*
        {
            this.self.playSound("fox_jumpflip");
        }

        internal function frame12():*
        {
            this.self.playSound("fox_jumpflip");
        }

        internal function frame19():*
        {
            this.self.endAttack();
        }


    }
}//package fox_fla

